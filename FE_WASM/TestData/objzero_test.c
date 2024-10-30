/*
https://github.com/jpcy/objzero

Copyright (c) 2018 Jonathan Young
Copyright (c) 2012-2018 Syoyo Fujita and many contributors.

The MIT License (MIT)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "objzero.h"

static void printModel(const objzModel *_model) {
	for (uint32_t i = 0; i < _model->numMaterials; i++) {
		objzMaterial *mat = &_model->materials[i];
		printf("Material %u '%s'\n", i, mat->name);
		printf("   opacity: %g\n", mat->opacity);
		printf("   ambient: %g %g %g\n", mat->ambient[0], mat->ambient[1], mat->ambient[2]);
		printf("   diffuse: %g %g %g\n", mat->diffuse[0], mat->diffuse[1], mat->diffuse[2]);
		printf("   emission: %g %g %g\n", mat->emission[0], mat->emission[1], mat->emission[2]);
		printf("   specular: %g %g %g\n", mat->specular[0], mat->specular[1], mat->specular[2]);
		printf("   specularExponent: %g\n", mat->specularExponent);
		if (mat->ambientTexture[0])
			printf("   ambientTexture: %s\n", mat->ambientTexture);
		if (mat->bumpTexture[0])
			printf("   bumpTexture: %s\n", mat->bumpTexture);
		if (mat->diffuseTexture[0])
			printf("   diffuseTexture: %s\n", mat->diffuseTexture);
		if (mat->emissionTexture[0])
			printf("   emissionTexture: %s\n", mat->emissionTexture);
		if (mat->specularTexture[0])
			printf("   specularTexture: %s\n", mat->specularTexture);
		if (mat->specularExponentTexture[0])
			printf("   specularExponentTexture: %s\n", mat->specularExponentTexture);
		if (mat->opacityTexture[0])
			printf("   opacityTexture: %s\n", mat->opacityTexture);
	}
	for (uint32_t i = 0; i < _model->numObjects; i++) {
		objzObject *object = &_model->objects[i];
		printf("Object: %u '%s', %u triangles, %u vertices, %u meshes\n", i, object->name, object->numIndices / 3, object->numVertices, object->numMeshes);
		for (uint32_t j = 0; j < object->numMeshes; j++) {
			objzMesh *mesh = &_model->meshes[object->firstMesh + j];
			printf("   Mesh %u: '%s' material, %u triangles\n", j, mesh->materialIndex < 0 ? "<empty>" : _model->materials[mesh->materialIndex].name, mesh->numIndices / 3);
		}
	}
	printf("%u objects\n", _model->numObjects);
	printf("%u materials\n", _model->numMaterials);
	printf("%u meshes\n", _model->numMeshes);
	printf("%u vertices\n", _model->numVertices);
	printf("%u triangles\n", _model->numIndices / 3);
}

static size_t s_totalBytesUsed = 0;
static size_t s_peakBytesUsed = 0;

// Custom realloc that tracks memory usage by prepending the size to every allocation.
static void *custom_realloc(void *_ptr, size_t _size) {
	uint32_t *realPtr = _ptr ? ((uint32_t *)_ptr) - 1 : NULL;
	if (!_size) {
		s_totalBytesUsed -= *realPtr;
		return realloc(realPtr, 0);
	}
	_size += 4;
	if (realPtr)
		s_totalBytesUsed -= *realPtr;
	uint32_t *newPtr = realloc(realPtr, _size);
	if (!newPtr)
		return NULL;
	*newPtr = (uint32_t)_size;
	s_totalBytesUsed += _size;
	if (s_totalBytesUsed > s_peakBytesUsed)
		s_peakBytesUsed = s_totalBytesUsed;
	return newPtr + 1;
}

static void progressCallback(const char *_filename, int _progress) {
	(void)_filename; // Not used.
	printf("\r[");
	for (int i = 0; i < 10; i++)
		printf(_progress / ((i + 1) * 10) ? "*" : " ");
	printf("] %d%%", _progress);
	fflush(stdout);
}

int main(int argc, char **argv) {
	if (argc <= 1)
		return 0;
	printf("Loading '%s'\n", argv[1]);
	objz_setProgress(progressCallback);
	objz_setRealloc(custom_realloc);
	// clock_t start = clock();
	objzModel *model = objz_load(argv[1]);
	// clock_t end = clock();
	printf("\n");
	if (!model) {
		printf("ERROR: %s\n", objz_getError());
		return 1;
	} else {
		const char *warning = objz_getError();
		if (warning)
			printf("%s\n", warning);
	}
	printModel(model);
	// printf("objz_load: %g ms, %0.2f MB\n", (end - start) * 1000.0 / (double)CLOCKS_PER_SEC, s_peakBytesUsed / 1024.0f / 1024.0f);
	objz_destroy(model);
	return 0;
}
