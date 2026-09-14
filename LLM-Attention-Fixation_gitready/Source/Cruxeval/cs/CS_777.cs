using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> names, string excluded) {
        if (string.IsNullOrEmpty(excluded))
        {
            return names;
        }
        for (int i = 0; i < names.Count; i++)
        {
            if (names[i].Contains(excluded))
            {
                names[i] = names[i].Replace(excluded, "");
            }
        }
        return names;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"avc  a .d e"})), ("")).SequenceEqual((new List<string>(new string[]{(string)"avc  a .d e"}))));
    }

}
