using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(string text) {
        var ls = text.Split(' ').ToList();
        var lines = string.Join(" ", ls.Where((str, i) => i % 3 == 0)).Split('\n').ToList();
        var res = new List<string>();
        for (int i = 0; 3 * i + 1 < ls.Count; i++)
        {
            var ln = ls.Where((str, idx) => idx % 3 == 1).ToList();
            if (3 * i + 1 < ln.Count)
            {
                res.Add(string.Join(" ", ln.Skip(3 * i).Take(3)));
            }
        }
        return lines.Concat(res).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("echo hello!!! nice!")).SequenceEqual((new List<string>(new string[]{(string)"echo"}))));
    }

}
