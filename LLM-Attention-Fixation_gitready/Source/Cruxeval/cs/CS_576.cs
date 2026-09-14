using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<long> array, long const_val) {
        List<string> output = new List<string>() { "x" };
        for (int i = 1; i <= array.Count; i++)
        {
            if (i % 2 != 0)
            {
                output.Add((-2 * array[i - 1]).ToString());
            }
            else
            {
                output.Add(const_val.ToString());
            }
        }
        return output;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L})), (-1L)).SequenceEqual((new List<string>(new string[]{(string)"x", (string)"-2", (string)"-1", (string)"-6"}))));
    }

}
