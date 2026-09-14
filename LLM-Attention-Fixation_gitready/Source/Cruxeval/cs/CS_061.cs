using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
using System.Globalization;
class Problem {
    public static string F(string text) {
        string[] texts = text.Split(new char[] { ' ' }, StringSplitOptions.RemoveEmptyEntries);
        if (texts.Length > 0)
        {
            var xtexts = texts.Where(t => t.All(ch => ch <= 0x7F) && t != "nada" && t != "0").ToList();
            return xtexts.Count > 0 ? xtexts.OrderByDescending(s => s.Length).First() : "nada";
        }
        return "nada";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("")).Equals(("nada")));
    }

}
