using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> places, List<long> lazy) {
        places.Sort();
        foreach (var l in lazy)
        {
            places.Remove(l);
        }
        if (places.Count == 1)
        {
            return 1;
        }
        for (int i = 0; i < places.Count; i++)
        {
            var place = places[i];
            if (places.Count(p => p == place + 1) == 0)
            {
                return i + 1;
            }
        }
        return places.Count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)375L, (long)564L, (long)857L, (long)90L, (long)728L, (long)92L})), (new List<long>(new long[]{(long)728L}))) == (1L));
    }

}
