using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(string test, string sep = " ", long maxsplit = -1) {
        try
        {
            return test.Split(new string[] { sep }, StringSplitOptions.None).Take((int)maxsplit).ToList();
        }
        catch
        {
            return test.Split().ToList();
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ab cd"), ("x"), (2L)).SequenceEqual((new List<string>(new string[]{(string)"ab cd"}))));
    }

}
