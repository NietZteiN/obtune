using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(string pattern, List<string> items) {
        List<long> result = new List<long>();
        foreach(var text in items)
        {
            int pos = text.LastIndexOf(pattern);
            if (pos >= 0)
            {
                result.Add(pos);
            }
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((" B "), (new List<string>(new string[]{(string)" bBb ", (string)" BaB ", (string)" bB", (string)" bBbB ", (string)" bbb"}))).SequenceEqual((new List<long>())));
    }

}
