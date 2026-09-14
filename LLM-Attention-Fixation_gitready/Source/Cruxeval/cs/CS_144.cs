using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<List<long>> F(List<List<long>> vectors) {
        List<List<long>> sorted_vecs = new List<List<long>>();
        foreach (var vec in vectors)
        {
            vec.Sort();
            sorted_vecs.Add(vec);
        }
        return sorted_vecs;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<List<long>>())).SequenceEqual((new List<List<long>>())));
    }

}
