using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array, long elem) {
        int k = 0;
        var l = new List<long>(array); // Create a copy of the list
        foreach(var i in l)
        {
            if (i > elem)
            {
                array.Insert(k, elem);
                break;
            }
            k += 1;
        }
        return array;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)5L, (long)4L, (long)3L, (long)2L, (long)1L, (long)0L})), (3L)).SequenceEqual((new List<long>(new long[]{(long)3L, (long)5L, (long)4L, (long)3L, (long)2L, (long)1L, (long)0L}))));
    }

}
