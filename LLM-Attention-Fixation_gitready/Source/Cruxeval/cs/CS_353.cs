using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> x) {
        if (x.Count == 0) {
            return -1;
        } else {
            Dictionary<long, int> cache = new Dictionary<long, int>();
            foreach (long item in x) {
                if (cache.ContainsKey(item)) {
                    cache[item]++;
                } else {
                    cache[item] = 1;
                }
            }
            return cache.Values.Max();
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)0L, (long)2L, (long)2L, (long)0L, (long)0L, (long)0L, (long)1L}))) == (4L));
    }

}
