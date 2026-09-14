using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(Dictionary<long,List<long>> d1, Dictionary<long,List<long>> d2) {
        int mmax = 0;
        foreach (var k1 in d1.Keys) {
            int p = d1[k1].Count + (d2.ContainsKey(k1) ? d2[k1].Count : 0);
            if (p > mmax) {
                mmax = p;
            }
        }
        return mmax;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<long,List<long>>(){{0L, new List<long>()}, {1L, new List<long>()}}), (new Dictionary<long,List<long>>(){{0L, new List<long>(new long[]{(long)0L, (long)0L, (long)0L, (long)0L})}, {2L, new List<long>(new long[]{(long)2L, (long)2L, (long)2L})}})) == (4L));
    }

}
