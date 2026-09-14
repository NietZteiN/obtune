using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array) {
        while (array.Contains(-1))
        {
            array.RemoveAt(array.Count - 3);
        }
        while (array.Contains(0))
        {
            array.RemoveAt(array.Count - 1);
        }
        while (array.Contains(1))
        {
            array.RemoveAt(0);
        }
        return array;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)0L, (long)2L}))).SequenceEqual((new List<long>())));
    }

}
