using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, List<string> rules) {
        foreach (var rule in rules)
        {
            if (rule == "@")
            {
                text = new string(text.Reverse().ToArray());
            }
            else if (rule == "~")
            {
                text = text.ToUpper();
            }
            else if (!string.IsNullOrEmpty(text) && text[text.Length - 1] == rule[0])
            {
                text = text.Substring(0, text.Length - 1);
            }
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("hi~!"), (new List<string>(new string[]{(string)"~", (string)"`", (string)"!", (string)"&"}))).Equals(("HI~")));
    }

}
