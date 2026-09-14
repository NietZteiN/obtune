using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> numbers, string prefix) {
        return numbers.Select(n => n.Length > prefix.Length && n.StartsWith(prefix)? n.Substring(prefix.Length) : n).OrderBy(n => n).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"ix", (string)"dxh", (string)"snegi", (string)"wiubvu"})), ("")).SequenceEqual((new List<string>(new string[]{(string)"dxh", (string)"ix", (string)"snegi", (string)"wiubvu"}))));
    }

}
