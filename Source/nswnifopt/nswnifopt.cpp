/*
nswnifopt: remove editor markers and optimize for SSE.
Copyright (c) 2019 Thy Woof

Based on work from Parco Opaai. See below.

nifopt: convert and optimize between NiTriShape and BSTriShape.
Copyright (C) 2018  Parco Opaai

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "NifFile.h"

// OptimizeForSSE function from
// https://github.com/ousnius/BodySlide-and-Outfit-Studio/blob/dev/lib/NIF/NifFile.cpp

struct OptOptionsSSE
{
	bool headParts = false;
	bool removeParallax = true;
	bool calcBounds = true;
};

struct OptResultSSE
{
	bool versionMismatch = false;
	bool dupesRenamed = false;
	std::vector<std::string> shapesVColorsRemoved;
	std::vector<std::string> shapesNormalsRemoved;
	std::vector<std::string> shapesPartTriangulated;
	std::vector<std::string> shapesTangentsAdded;
	std::vector<std::string> shapesParallaxRemoved;
};


bool RemoveEditorMarkers(NifFile& nif)
{
	bool changed = false;
	NiHeader& hdr = nif.GetHeader();
	NiVersion& version = hdr.GetVersion();

	if (version.User() != 12) {
		return changed;
	}

	for (auto &shape : nif.GetShapes()) {
		std::string shapeName = shape->GetName();

		if (shapeName == "EditorMarker") {
			printf("Found an editor marker. Deleting...\n");
			nif.DeleteShape(shape);
			changed = true;
		}
	}
	
	return changed;
}

OptResultSSE RemoveAndOptimizeForSSE(NifFile& nif, const OptOptionsSSE& options = OptOptionsSSE())
{
	OptResultSSE result;

	NiHeader& hdr = nif.GetHeader();
	NiVersion& version = hdr.GetVersion();

	if (version.User() != 12) {
		result.versionMismatch = true;
		return result;
	}

	if (!nif.IsTerrain())
		result.dupesRenamed = nif.RenameDuplicateShapes();

	version.SetFile(V20_2_0_7);
	version.SetUser(12);
	version.SetStream(100);

	for (auto &shape : nif.GetShapes()) {
		std::string shapeName = shape->GetName();

		if (shapeName == "EditorMarker") {
			printf("Found an editor marker. Deleting...\n");
			nif.DeleteShape(shape);
			continue;
		}

		auto geomData = hdr.GetBlock<NiGeometryData>(shape->GetDataRef());
		if (geomData) {
			bool removeVertexColors = true;
			bool hasTangents = geomData->HasTangents();
			std::vector<Vector3>* vertices = &geomData->vertices;
			std::vector<Vector3>* normals = &geomData->normals;
			const std::vector<Color4>& colors = geomData->vertexColors;
			std::vector<Vector2>* uvs = nullptr;
			if (!geomData->uvSets.empty())
				uvs = &geomData->uvSets[0];

			std::vector<Triangle> triangles;
			geomData->GetTriangles(triangles);

			// Only remove vertex colors if all are 0xFFFFFFFF
			Color4 white(1.0f, 1.0f, 1.0f, 1.0f);
			for (auto &c : colors) {
				if (white != c) {
					removeVertexColors = false;
					break;
				}
			}

			bool headPartEyes = false;
			NiShader* shader = nif.GetShader(shape);
			if (shader) {
				auto bslsp = dynamic_cast<BSLightingShaderProperty*>(shader);
				if (bslsp) {
					// Remember eyes flag for later
					if ((bslsp->shaderFlags1 & (1 << 17)) != 0)
						headPartEyes = true;

					// No normals and tangents with model space maps
					if ((bslsp->shaderFlags1 & (1 << 12)) != 0) {
						if (!normals->empty())
							result.shapesNormalsRemoved.push_back(shapeName);

						normals = nullptr;
					}

					// Check tree anim flag
					if ((bslsp->shaderFlags2 & (1 << 29)) != 0)
						removeVertexColors = false;

					// Disable flag if vertex colors were removed
					if (removeVertexColors)
						bslsp->shaderFlags2 &= ~(1 << 5);

					if (options.removeParallax) {
						if (bslsp->GetShaderType() == BSLSP_PARALLAX) {
							// Change type from parallax to default
							bslsp->SetShaderType(BSLSP_DEFAULT);

							// Remove parallax flag
							bslsp->shaderFlags1 &= ~(1 << 11);

							// Remove parallax texture from set
							auto textureSet = hdr.GetBlock<BSShaderTextureSet>(shader->GetTextureSetRef());
							if (textureSet && textureSet->numTextures >= 4)
								textureSet->textures[3].Clear();

							result.shapesParallaxRemoved.push_back(shapeName);
						}
					}
				}

				auto bsesp = dynamic_cast<BSEffectShaderProperty*>(shader);
				if (bsesp) {
					// Remember eyes flag for later
					if ((bsesp->shaderFlags1 & (1 << 17)) != 0)
						headPartEyes = true;

					// Check tree anim flag
					if ((bsesp->shaderFlags2 & (1 << 29)) != 0)
						removeVertexColors = false;

					// Disable flag if vertex colors were removed
					if (removeVertexColors)
						bsesp->shaderFlags2 &= ~(1 << 5);
				}
			}

			if (!colors.empty() && removeVertexColors)
				result.shapesVColorsRemoved.push_back(shapeName);

			BSTriShape* bsOptShape = nullptr;
			auto bsSegmentShape = dynamic_cast<BSSegmentedTriShape*>(shape);
			if (bsSegmentShape) {
				bsOptShape = new BSSubIndexTriShape();
			}
			else {
				if (options.headParts)
					bsOptShape = new BSDynamicTriShape();
				else
					bsOptShape = new BSTriShape();
			}

			bsOptShape->SetName(shape->GetName());
			bsOptShape->SetControllerRef(shape->GetControllerRef());
			bsOptShape->SetSkinInstanceRef(shape->GetSkinInstanceRef());
			bsOptShape->SetShaderPropertyRef(shape->GetShaderPropertyRef());
			bsOptShape->SetAlphaPropertyRef(shape->GetAlphaPropertyRef());
			bsOptShape->SetCollisionRef(shape->GetCollisionRef());
			bsOptShape->GetProperties() = shape->GetProperties();
			bsOptShape->GetExtraData() = shape->GetExtraData();

			bsOptShape->transform = shape->transform;

			bsOptShape->Create(vertices, &triangles, uvs, normals);
			bsOptShape->flags = shape->flags;

			// Move segments to new shape
			if (bsSegmentShape) {
				auto bsSITS = dynamic_cast<BSSubIndexTriShape*>(bsOptShape);
				bsSITS->numSegments = bsSegmentShape->numSegments;
				bsSITS->segments = bsSegmentShape->segments;
			}

			// Restore old bounds for static meshes or when calc bounds is off
			if (!shape->IsSkinned() || !options.calcBounds)
				bsOptShape->SetBounds(geomData->GetBounds());

			// Vertex Colors
			if (bsOptShape->GetNumVertices() > 0) {
				if (!removeVertexColors && colors.size() > 0) {
					bsOptShape->SetVertexColors(true);
					for (int i = 0; i < bsOptShape->GetNumVertices(); i++) {
						auto& vertex = bsOptShape->vertData[i];

						float f = std::max(0.0f, std::min(1.0f, colors[i].r));
						vertex.colorData[0] = (byte)std::floor(f == 1.0f ? 255 : f * 256.0);

						f = std::max(0.0f, std::min(1.0f, colors[i].g));
						vertex.colorData[1] = (byte)std::floor(f == 1.0f ? 255 : f * 256.0);

						f = std::max(0.0f, std::min(1.0f, colors[i].b));
						vertex.colorData[2] = (byte)std::floor(f == 1.0f ? 255 : f * 256.0);

						f = std::max(0.0f, std::min(1.0f, colors[i].a));
						vertex.colorData[3] = (byte)std::floor(f == 1.0f ? 255 : f * 256.0);
					}
				}

				// Find NiOptimizeKeep string
				for (auto& extraData : bsOptShape->GetExtraData()) {
					auto stringData = hdr.GetBlock<NiStringExtraData>(extraData.GetIndex());
					if (stringData) {
						if (stringData->GetStringData().find("NiOptimizeKeep") != std::string::npos) {
							bsOptShape->particleDataSize = bsOptShape->GetNumVertices() * 6 + triangles.size() * 3;
							bsOptShape->particleVerts = *vertices;

							bsOptShape->particleNorms.resize(vertices->size(), Vector3(1.0f, 0.0f, 0.0f));
							if (normals && normals->size() == vertices->size())
								bsOptShape->particleNorms = *normals;

							bsOptShape->particleTris = triangles;
						}
					}
				}

				// Skinning and partitions
				if (shape->IsSkinned()) {
					bsOptShape->SetSkinned(true);

					auto skinInst = hdr.GetBlock<NiSkinInstance>(shape->GetSkinInstanceRef());
					if (skinInst) {
						auto skinPart = hdr.GetBlock<NiSkinPartition>(skinInst->GetSkinPartitionRef());
						if (skinPart) {
							bool triangulated = nif.TriangulatePartitions(shape);
							if (triangulated)
								result.shapesPartTriangulated.push_back(shapeName);

							for (int partID = 0; partID < skinPart->numPartitions; partID++) {
								NiSkinPartition::PartitionBlock& part = skinPart->partitions[partID];

								for (int i = 0; i < part.numVertices; i++) {
									const ushort v = part.vertexMap[i];

									if (bsOptShape->vertData.size() > v) {
										auto& vertex = bsOptShape->vertData[v];

										if (part.hasVertexWeights) {
											auto& weights = part.vertexWeights[i];
											vertex.weights[0] = weights.w1;
											vertex.weights[1] = weights.w2;
											vertex.weights[2] = weights.w3;
											vertex.weights[3] = weights.w4;
										}

										if (part.hasBoneIndices) {
											auto& boneIndices = part.boneIndices[i];
											vertex.weightBones[0] = part.bones[boneIndices.i1];
											vertex.weightBones[1] = part.bones[boneIndices.i2];
											vertex.weightBones[2] = part.bones[boneIndices.i3];
											vertex.weightBones[3] = part.bones[boneIndices.i4];
										}
									}
								}

								std::vector<Triangle> realTris(part.numTriangles);
								for (int i = 0; i < part.numTriangles; i++) {
									auto& partTri = part.triangles[i];

									// Find the actual tri index from the partition tri index
									Triangle tri;
									tri.p1 = part.vertexMap[partTri.p1];
									tri.p2 = part.vertexMap[partTri.p2];
									tri.p3 = part.vertexMap[partTri.p3];

									tri.rot();
									realTris[i] = tri;
								}

								part.triangles = realTris;
								part.trueTriangles = realTris;
							}
						}
					}
				}
				else
					bsOptShape->SetSkinned(false);
			}
			else
				bsOptShape->SetVertices(false);

			// Check if tangents were added
			if (!hasTangents && bsOptShape->HasTangents())
				result.shapesTangentsAdded.push_back(shapeName);

			// Enable eye data flag
			if (!bsSegmentShape) {
				if (options.headParts) {
					if (headPartEyes)
						bsOptShape->SetEyeData(true);
				}
			}

			hdr.ReplaceBlock(nif.GetBlockID(shape), bsOptShape);
			nif.UpdateSkinPartitions(bsOptShape);
		}
	}

	nif.DeleteUnreferencedBlocks();

	// For files without a root node, remove the leftover data blocks anyway
	hdr.DeleteBlockByType("NiTriStripsData", true);
	hdr.DeleteBlockByType("NiTriShapeData", true);

	return result;
}

int main(int argc, char* const argv[], char* const envp[])
{
	if (argc != 3) {
		std::cout << "Usage: nswnifopt.exe [RemoveMarkers|RemoveAndOptimize] input.nif" << std::endl;
		return 1;
	}

	char* command = argv[1];

	if (!(strcmp(command, "RemoveMarkers") == 0 || strcmp(command, "RemoveAndOptimize") == 0)) {
		std::cout << "Usage: nswnifopt.exe [RemoveMarkers|RemoveAndOptimize] input.nif" << std::endl;
		return 1;	
	}

	NifFile nif;

	char* filename = argv[2];
	
	nif.Load(filename);

	NiHeader& hdr = nif.GetHeader();
	NiVersion& version = hdr.GetVersion();

	printf("NiVersion file: 0x%08x user: %u stream: %u\n", version.File(), version.User(), version.Stream());

	if (version.File() != 0x14020007) {
		printf("not supported.\n");
		return 0;
	}

	if (version.User() == 12) {
		bool changed;

		if (strcmp(command, "RemoveMarkers") == 0) {
			printf("Remove Editor Markers.\n");
			changed = RemoveEditorMarkers(nif);
		} else if (strcmp(command, "RemoveAndOptimize") == 0)
		{
			printf("Remove Editor Markers and optimize for SSE.\n");
			RemoveAndOptimizeForSSE(nif);
			changed = true;
		}
		if (changed) {
			nif.Save(filename);
		}
	}
	else {
		printf("not supported.\n");
		return 0;
	}

	return 0;
}
