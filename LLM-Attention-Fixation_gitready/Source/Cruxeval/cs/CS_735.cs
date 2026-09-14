using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string sentence) {
        if (sentence == "")
            return "";
        sentence = sentence.Replace("(", "");
        sentence = sentence.Replace(")", "");
        sentence = char.ToUpper(sentence[0]) + sentence.Substring(1).ToLower();
        sentence = sentence.Replace(" ", "");
        return sentence;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("(A (b B))")).Equals(("Abb")));
    }

}
