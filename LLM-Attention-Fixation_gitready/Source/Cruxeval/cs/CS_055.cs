using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> array) {
        List<long> array_2 = new List<long>();
        foreach (var i in array)
        {
            if (i > 0)
            {
                array_2.Add(i);
            }
        }
        array_2.Sort();
        array_2.Reverse();
        return array_2;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)4L, (long)8L, (long)17L, (long)89L, (long)43L, (long)14L}))).SequenceEqual((new List<long>(new long[]{(long)89L, (long)43L, (long)17L, (long)14L, (long)8L, (long)4L}))));
    }

}
