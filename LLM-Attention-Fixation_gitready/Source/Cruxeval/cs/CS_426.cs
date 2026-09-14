using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;

class Problem {
    public static List<long> F(List<long> numbers, long elem, long idx) {
        if (idx >= numbers.Count) {
            numbers.Add(elem);
        } else {
            numbers.Insert((int)idx, elem);
        }
        return numbers;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L})), (8L), (5L)).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L, (long)3L, (long)8L}))));
    }

}
