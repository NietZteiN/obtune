using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(string s, long n) {
        List<string> ls = s.Split(' ').ToList();
        List<string> out_list = new List<string>();
        while (ls.Count >= n)
        {
            out_list.AddRange(ls.TakeLast((int)n).ToList());
            ls.RemoveRange((int)(ls.Count - n), (int)n);
        }
        List<string> result = ls;
        result.Add(string.Join("_", out_list));
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("one two three four five"), (3L)).SequenceEqual((new List<string>(new string[]{(string)"one", (string)"two", (string)"three_four_five"}))));
    }

}
