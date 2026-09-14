using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(Dictionary<string,long> d) {
        int size = d.Count;
        List<long> v = new List<long>(new long[size]);
        if (size == 0)
        {
            return v;
        }
        for (int i = 0; i < d.Count; i++)
        {
            v[i] = d.ElementAt(i).Value;
        }
        return v;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,long>(){{"a", 1L}, {"b", 2L}, {"c", 3L}})).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L, (long)3L}))));
    }

}
