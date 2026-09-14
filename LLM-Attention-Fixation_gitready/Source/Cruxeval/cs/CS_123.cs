using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array, long elem) {
        for (int idx = 0; idx < array.Count; idx++)
        {
            if (array[idx] > elem && idx > 0 && array[idx - 1] < elem)
            {
                array.Insert(idx, elem);
                break;  // Only add once
            }
        }
        return array;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L, (long)5L, (long)8L})), (6L)).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L, (long)3L, (long)5L, (long)6L, (long)8L}))));
    }

}
