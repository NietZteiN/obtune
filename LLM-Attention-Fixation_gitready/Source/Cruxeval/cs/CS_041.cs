using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array, List<long> values) {
        array.Reverse();
        foreach (var value in values)
        {
            array.Insert(array.Count / 2, value);
        }
        array.Reverse();
        return array;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)58L})), (new List<long>(new long[]{(long)21L, (long)92L}))).SequenceEqual((new List<long>(new long[]{(long)58L, (long)92L, (long)21L}))));
    }

}
