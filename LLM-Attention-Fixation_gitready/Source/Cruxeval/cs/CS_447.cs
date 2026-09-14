using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long tab_size) {
        string res = "";
        text = text.Replace("\t", new string(' ', (int)tab_size-1));
        for (int i = 0; i < text.Length; i++)
        {
            if (text[i] == ' ')
            {
                res += "|";
            }
            else
            {
                res += text[i];
            }
        }
        return res;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("	a"), (3L)).Equals(("||a")));
    }

}
