using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(string text, string elem) {
        if (elem != "") {
            while (text.StartsWith(elem)) {
                text = text.Replace(elem, "");
            }
            while (elem.StartsWith(text)) {
                elem = elem.Replace(text, "");
            }
        }
        return new List<string> {elem, text};
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("some"), ("1")).SequenceEqual((new List<string>(new string[]{(string)"1", (string)"some"}))));
    }

}
