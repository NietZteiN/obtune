using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array) {
        List<long> result = new List<long>();
        int index = 0;
        while (index < array.Count)
        {
            result.Add(array[array.Count - 1]);
            array.RemoveAt(array.Count - 1);
            index += 2;
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)8L, (long)8L, (long)-4L, (long)-9L, (long)2L, (long)8L, (long)-1L, (long)8L}))).SequenceEqual((new List<long>(new long[]{(long)8L, (long)-1L, (long)8L}))));
    }

}
