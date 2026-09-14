using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static Tuple<long, string> F(string text, string lower, string upper) {
        long count = 0;
        List<string> new_text = new List<string>();
        foreach(var char1 in text)
        {
            string char2 = char.IsDigit(char1) ? lower : upper;
            if (new string[] { "p", "C" }.Contains(char2))
            {
                count += 1;
            }
            new_text.Add(char2);
        }
        return Tuple.Create(count, string.Join("", new_text));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("DSUWeqExTQdCMGpqur"), ("a"), ("x")).Equals((Tuple.Create(0L, "xxxxxxxxxxxxxxxxxx"))));
    }

}
