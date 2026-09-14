using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(List<string> strings, string substr) {
        var list = strings.Where(s => s.StartsWith(substr)).ToList();
        list.Sort((x, y) => x.Length.CompareTo(y.Length));
        return list;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<string>(new string[]{(string)"condor", (string)"eyes", (string)"gay", (string)"isa"})), ("d")).SequenceEqual((new List<string>())));
    }

}
