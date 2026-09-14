using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string chars) {
        var listchars = new List<char>(chars);
        char first = listchars[listchars.Count - 1];
        listchars.RemoveAt(listchars.Count - 1);
        foreach (char i in listchars)
        {
            text = text.Substring(0, text.IndexOf(i)) + i + text.Substring(text.IndexOf(i) + 1);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("tflb omn rtt"), ("m")).Equals(("tflb omn rtt")));
    }

}
