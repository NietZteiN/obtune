using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(string text) {
        var new_text = new List<string>();
        for (int i = 0; i < text.Length / 3; i++)
        {
            new_text.Add($"< {text.Substring(i * 3, 3)} level={i} >");
        }
        var last_item = text.Substring(text.Length / 3 * 3);
        new_text.Add($"< {last_item} level={text.Length / 3} >");
        return new_text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("C7")).SequenceEqual((new List<string>(new string[]{(string)"< C7 level=0 >"}))));
    }

}
