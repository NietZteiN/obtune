using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> L) {
        int N = L.Count;
        for (int k = 1; k <= N / 2; k++)
        {
            int i = k - 1;
            int j = N - k;
            while (i < j)
            {
                // swap elements:
                long temp = L[i];
                L[i] = L[j];
                L[j] = temp;
                // update i, j:
                i++;
                j--;
            }
        }
        return L;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)16L, (long)14L, (long)12L, (long)7L, (long)9L, (long)11L}))).SequenceEqual((new List<long>(new long[]{(long)11L, (long)14L, (long)7L, (long)12L, (long)9L, (long)16L}))));
    }

}
