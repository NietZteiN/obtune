using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(Dictionary<long,long> d, long index) {
        long length = d.Count;
        long idx = index % length;
        long v = d.Last().Value;
        for (long i = 0; i < idx; i++)
        {
            d.Remove(d.Last().Key);
        }
        return v;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<long,long>(){{27L, 39L}}), (1L)) == (39L));
    }

}
