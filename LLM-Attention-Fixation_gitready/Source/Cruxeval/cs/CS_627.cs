using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<Tuple<string, long>> parts) {
        var dictionary = new Dictionary<string, long>();
        foreach (var part in parts)
        {
            dictionary[part.Item1] = part.Item2;
        }
        return dictionary.Values.ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<Tuple<string, long>>(new Tuple<string, long>[]{(Tuple<string, long>)Tuple.Create("u", 1L), (Tuple<string, long>)Tuple.Create("s", 7L), (Tuple<string, long>)Tuple.Create("u", -5L)}))).SequenceEqual((new List<long>(new long[]{(long)-5L, (long)7L}))));
    }

}
