using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array, long index, long value) {
        array.Insert(0, index + 1);
        if (value >= 1) {
            array.Insert((int)index, value);
        }
        return array;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)2L})), (0L), (2L)).SequenceEqual((new List<long>(new long[]{(long)2L, (long)1L, (long)2L}))));
    }

}
