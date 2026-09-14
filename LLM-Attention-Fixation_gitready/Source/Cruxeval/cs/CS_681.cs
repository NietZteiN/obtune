using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array, long ind, long elem) {
        if (ind < 0)
        {
            array.Insert(-5, elem);
        }
        else if (ind > array.Count)
        {
            array.Insert(array.Count, elem);
        }
        else
        {
            array.Insert((int)(ind + 1), elem);
        }
        return array;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)5L, (long)8L, (long)2L, (long)0L, (long)3L})), (2L), (7L)).SequenceEqual((new List<long>(new long[]{(long)1L, (long)5L, (long)8L, (long)7L, (long)2L, (long)0L, (long)3L}))));
    }

}
