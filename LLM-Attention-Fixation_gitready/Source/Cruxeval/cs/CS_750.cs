using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(Dictionary<string,string> char_map, string text) {
        string new_text = "";
        foreach (char ch in text)
        {
            if (char_map.TryGetValue(ch.ToString(), out string val))
            {
                new_text += val;
            }
            else
            {
                new_text += ch;
            }
        }
        return new_text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,string>()), ("hbd")).Equals(("hbd")));
    }

}
