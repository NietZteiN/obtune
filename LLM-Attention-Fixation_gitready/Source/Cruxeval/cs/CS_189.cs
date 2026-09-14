using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
using System.Text.RegularExpressions;

class Problem {
    public static string F(string outStr, Dictionary<string,List<string>> mapping) {
        foreach(var key in mapping.Keys.ToList())
        {
            outStr = String.Format(outStr, mapping);
            if (Regex.Matches(outStr, @"{\w}").Count == 0)
            {
                break;
            }
            mapping[key][1] = new string(mapping[key][1].ToCharArray().Reverse().ToArray());
        }
        return outStr;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("{{{{}}}}"), (new Dictionary<string,List<string>>())).Equals(("{{{{}}}}")));
    }

}
