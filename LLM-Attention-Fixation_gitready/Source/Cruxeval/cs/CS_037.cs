using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(string text) {
        var text_arr = new List<string>();
        for (int j = 0; j < text.Length; j++)
        {
            text_arr.Add(text.Substring(j));
        }
        return text_arr;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("123")).SequenceEqual((new List<string>(new string[]{(string)"123", (string)"23", (string)"3"}))));
    }

}
