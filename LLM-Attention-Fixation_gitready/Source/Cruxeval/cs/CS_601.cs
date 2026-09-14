using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        int t = 5;
        List<string> tab = new List<string>();
        foreach (char i in text) {
            if ("aeiouy".Contains(char.ToLower(i))) {
                tab.Add(new string(i.ToString().ToUpper()[0], t));
            }
            else {
                tab.Add(new string(i, t));
            }
        }
        return string.Join(" ", tab);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("csharp")).Equals(("ccccc sssss hhhhh AAAAA rrrrr ppppp")));
    }

}
