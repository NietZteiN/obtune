using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array) {
        List<long> new_array = new List<long>(array);
        new_array.Reverse();
        for(int i = 0; i < new_array.Count; i++)
        {
            new_array[i] = new_array[i] * new_array[i];
        }
        return new_array;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)1L}))).SequenceEqual((new List<long>(new long[]{(long)1L, (long)4L, (long)1L}))));
    }

}
