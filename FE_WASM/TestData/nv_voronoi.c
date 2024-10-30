// nv_voronoi.h - implementation of a fast, integer-based voronoi rasterization algorithm.
//
// Version 1.01; released to the public domain. No warranty implied; use at own risk.
//
// This is a small implementation of the method for Voronoi cell generation, using the method described in
// "Linear Time Euclidean Distance Algorithms" by Breu et al. It only uses integer arithmetic, meaning that it should be
// deterministic. The paper itself is pretty vague on a bunch of things; in particular, it never explains how you actually
// *use* the list of voronoi centers that you are given to render the resulting image (answer: use the perpendicular bisector
// calculation.)
//
// You might want to use this if you are deterministically generating terrain over a network, or if you need Euclidean distance
// (from, say, obstacles.) 
//
// If you find this useful, a thank you in your credits would be appreciated.
//
// -- Nicholas Vining (nicholas dot vining 'at' gas lamp games dot com)
//
// REVISION HISTORY:
//
//			version 1.0  - initial version
//			version 1.01 - moved implementation outside of guard header 

#ifndef __NV_INTEGERVORONOI_H_
#define __NV_INTEGERVORONOI_H_

void linear_time_voronoi ( int num_points, int *feature_points, int *dest, int w, int h );

#endif

#define false 0
#define true 1
#define bool int

// #ifdef __NV_INTEGERVORONOI_IMPLEMENTATION

#include <stdlib.h>
#include <limits.h>

static int voronoi_perpendicular_bisector (int ux, int uy, int vx, int vy, int r )
{
	return ((vx*vx)-(ux*ux)-(2*r*(vy-uy))+(vy*vy)-(uy*uy)) / (2*(vx-ux));
}

static bool remove_candidate (int ux, int uy, int vx, int vy, int wx, int wy, int r)
{
	int a = ((wx - vx) * ((vx*vx)-(ux*ux)-(2*r*(vy-uy))+(vy*vy)-(uy*uy))); 
	int b = ((vx-ux)*((wx*wx)-(vx*vx)-(2*r*(wy-vy))+(wy*wy)-(vy*vy)));
	return a >= b;
}

static int compare_two_feature_points (const void * a, const void * b)
{
	int *x = (int *)a;
	int *y = (int *)b;

	if (x[1] > y[1])
	{
		return 1;
	}
	if (x[1] < y[1])
	{
		return -1;
	}
	if (x[0] < y[0])
	{
		return -1;
	}
	if (x[0] > y[0])
	{
		return 1;
	}
	return 0;
}

static void build_candidates (int *candidates, int num_points, int *feature_points, int w, int h, bool flipped )
{
	for (int i = 0; i < w*h; i++)
	{
		candidates[i] = -1;			// no candidate point found yet
	}

	if (flipped)
	{
		for (int i = 0; i < num_points; i++)
		{
			if (feature_points[i*2+1] == h-1)
			{
				candidates[(h-1)*w+feature_points[i*2+0]] = i;
			}
		}

		for (int j = h-2; j >= 0; j--)
		{
			for (int i = 0; i < w; i++)
			{
				candidates[j*w+i] = candidates[(j+1)*w+i];
			}
			for (int i = num_points-1; i >= 0; i--)
			{
				if (feature_points[i*2+1] == j)
				{
					candidates[j*w+feature_points[i*2+0]] = i;
				}
				if (feature_points[i*2+1] < j)
				{
					break;			// STOP!
				}
			}
		}
	}
	else
	{
		for (int i = 0; i < num_points; i++)
		{
			if (feature_points[i*2+1] == 0)
			{
				candidates[feature_points[i*2+0]] = i;
			}
			if (feature_points[i*2+1] > 0)
			{
				break;
			}
		}

		// build candidates

		for (int j = 1; j < h; j++)
		{
			for (int i = 0; i < w; i++)
			{
				candidates[j*w+i] = candidates[(j-1)*w+i];
			}
			for (int i = 0; i < num_points; i++)
			{
				if (feature_points[i*2+1] == j)
				{
					candidates[j*w+feature_points[i*2+0]] = i;
				}
				if (feature_points[i*2+1] > j)
				{
					break;			// STOP!
				}
			}
		}
	}
}

static void possibly_write(int x, int y, int *old_val, int new_val, int *feature_points)
{
	if (*old_val == -1)
	{
		*old_val = new_val;
	}
	else
	{
		int old_x = feature_points[(*old_val)*2+0] - x;
		int old_y = feature_points[(*old_val)*2+1] - y;
		int new_x = feature_points[new_val*2+0] - x;
		int new_y = feature_points[new_val*2+1] - y;

		int old_dist = old_x*old_x + old_y * old_y;
		int new_dist = new_x*new_x + new_y * new_y;

		// Have a face-off. Which am I closer to?

		if (old_dist > new_dist)
		{
			*old_val = new_val;
		}
	}
}

static void inner_loop( int *candidates, int num_points, int *feature_points, int *dest, int w, int h, bool flipped )
{
	int *candidate_row = (int *)malloc(w * sizeof(int));
	int *l_row = (int *)malloc(w * sizeof(int));
	int *centers = (int *)malloc(w*sizeof(int));

	for (int i = flipped ? h-1 : 0; flipped ? (i >= 0) : (i < h); (flipped ? i-- : i++))
	{
		int target_i = i;

		// for each row, we compute:
		//
		// candidates - all points that COULD be in L_r
		// L_r - all points that are actual voronoi centers that intersect with the row R

		int num_candidates = 0;
		int num_l = 0;
		int k = 1;
		int l = 2;

		for (int j = 0; j < w; j++)
		{
			if (candidates[i*w+j] != -1)
			{
				candidate_row[num_candidates] = candidates[i*w+j];
				num_candidates++;
			}
		}

		if (num_candidates == 0)
		{
			continue;
		}
		if (num_candidates == 1)
		{
			for (int j = 0; j < w; j++)
			{
				possibly_write(j, target_i, &dest[target_i*w+j], candidate_row[0], feature_points);
			}
			continue;
		}

		if (num_candidates > 0)
		{
			l_row[0] = candidate_row[0];
			num_l++;
		}
		if (num_candidates > 1)
		{
			l_row[1] = candidate_row[1];
			num_l++;
		}

		if (num_candidates == 2)
		{
			for (int j = 0; j < feature_points[l_row[0]*2+0]; j++)
			{
				possibly_write(j, target_i, &dest[target_i*w+j], l_row[0], feature_points);
			}
			for (int j = feature_points[l_row[0]*2+0]; j < feature_points[l_row[1]*2+0]; j++)
			{
				int distX1 = feature_points[l_row[0]*2+0] - j;
				int distY1 = feature_points[l_row[0]*2+1] - target_i;
				int distX2 = feature_points[l_row[1]*2+0] - j;
				int distY2 = feature_points[l_row[1]*2+1] - target_i;

				if (distX1*distX1+distY1*distY1 < distX2*distX2+distY2*distY2)
				{
					possibly_write(j, target_i, &dest[target_i*w+j], l_row[0], feature_points);
				}
				else
				{
					possibly_write(j, target_i, &dest[target_i*w+j], l_row[1], feature_points);
				}
			}
			for (int j = feature_points[l_row[1]*2+0]; j < w; j++)
			{
				possibly_write(j, target_i, &dest[target_i*w+j], l_row[1], feature_points);
			}
			continue;
		}

		// This is slightly different from the paper because they start their tables numbered at 1; yech
		while (l < num_candidates)
		{
			int w = candidate_row[l];
			while (k >= 1 && remove_candidate(
				feature_points[l_row[k-1]*2+0],
				feature_points[l_row[k-1]*2+1],
				feature_points[l_row[k]*2+0],
				feature_points[l_row[k]*2+1],
				feature_points[w*2+0],
				feature_points[w*2+1],
				i))
			{
				k = k - 1;
			}
			k = k + 1;
			l = l + 1;
			l_row[k] = w;
		}

		for (int j = 0; j < k; j++)
		{
			centers[j] = voronoi_perpendicular_bisector(
				feature_points[l_row[j]*2+0],
				feature_points[l_row[j]*2+1],
				feature_points[l_row[j+1]*2+0],
				feature_points[l_row[j+1]*2+1],
				i);
			if (centers[j] < 0)
			{
				centers[j] = 0;
			}
			if (centers[j] > w-1)
			{
				centers[j] = w-1;
			}
		}

		for (int j = 0; j < centers[0]; j++)
		{
			possibly_write(j, target_i, &dest[target_i*w+j], l_row[0], feature_points);
		}


		for (int m = 0; m < k-1; m++)
		{
			for (int j = centers[m];
				j < centers[m+1];
				j++)
			{
				int distX1 = feature_points[l_row[m]*2+0] - j;
				int distY1 = feature_points[l_row[m]*2+1] - target_i;
				int distX2 = feature_points[l_row[m+1]*2+0] - j;
				int distY2 = feature_points[l_row[m+1]*2+1] - target_i;

				if (distX1*distX1+distY1*distY1 < distX2*distX2+distY2*distY2)
				{
					possibly_write(j, target_i, &dest[target_i*w+j], l_row[m], feature_points);
				}
				else
				{
					possibly_write(j, target_i, &dest[target_i*w+j], l_row[m+1], feature_points);
				}
			}
		}

		for (int j = centers[k-1]; j < w; j++)
		{
			possibly_write(j, target_i, &dest[target_i*w+j], l_row[k], feature_points);
		}
	}

	free(candidate_row);
	free(l_row);
	free(centers);
}

void linear_time_voronoi ( int num_points, int *feature_points, int *dest, int w, int h )
{
	int *candidates;

	qsort(feature_points, num_points, sizeof(int)*2, compare_two_feature_points);

	for (int i = 0; i < w*h; i++)
	{
		dest[i] = -1;
	}

	candidates = (int *)malloc(w*h*sizeof(int));

	build_candidates(candidates, num_points, feature_points, w, h, false);
	inner_loop(candidates, num_points, feature_points, dest, w, h, false);

	// build candidates

	build_candidates(candidates, num_points, feature_points, w, h, true);
	inner_loop(candidates, num_points, feature_points, dest, w, h, true);

	free(candidates);
}


// #ifdef TEST_VORONOI

#include <stdio.h>

int main ( int argc, char *argv[] )
{
	// Test harness

	int num_points = 64;
	int width = 512;
	int height = 512;
	int *points = (int *)malloc(num_points * 2 * sizeof(int));
	int *dest = (int *)malloc(width*height*sizeof(int));
	for (int i = 0; i < num_points; i++)
	{
		points[i*2+0] = rand() % width;
		points[i*2+1] = rand() % height;
	}
	linear_time_voronoi(num_points, points, dest, width, height);

	for (int i = 0; i < num_points; i++)
	{
		dest[points[i*2+1]*width+points[i*2+0]] = -1;
	}

	{
		for (int i = 0; i < width * height; i++)
		{
			unsigned char val;
			if (dest[i] == -1)
			{
				val = 255;
			}
			else
			{
				val = dest[i] * (255 / num_points);
			}
			fwrite(&val, 1, 1, stdout);
		}		
	}
	return 0;
}
// #endif		// TEST_VORONOI

// #endif
