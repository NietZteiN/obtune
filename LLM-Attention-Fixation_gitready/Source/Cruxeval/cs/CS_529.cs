using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array) {
        long prev = array[0];
        List<long> newArray = new List<long>(array);
        for (int i = 1; i < array.Count; i++)
        {
            if (prev != array[i])
            {
                newArray[i] = array[i];
            }
            else
            {
                newArray.RemoveAt(i);
            }
            prev = array[i];
        }
        return newArray;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L}))).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L, (long)3L}))));
    }

}
