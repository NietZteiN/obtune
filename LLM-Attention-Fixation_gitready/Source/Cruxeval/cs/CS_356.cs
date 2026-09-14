using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array, long num) {
        bool reverse = false;
        if (num < 0)
        {
            reverse = true;
            num *= -1;
        }
        array.Reverse();
        array = Enumerable.Repeat(array, (int)num).SelectMany(x => x).ToList();
        
        if (reverse)
        {
            array.Reverse();
        }
        return array;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L})), (1L)).SequenceEqual((new List<long>(new long[]{(long)2L, (long)1L}))));
    }

}
