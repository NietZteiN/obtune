using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> array) {
        List<string> c = array;
        List<string> array_copy = array;

        while (true)
        {
            c.Add("_");
            if (c.SequenceEqual(array_copy))
            {
                array_copy[c.IndexOf("_")] = "";
                break;
            }
        }
        return array_copy;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>())).SequenceEqual((new List<string>(new string[]{(string)""}))));
    }

}
