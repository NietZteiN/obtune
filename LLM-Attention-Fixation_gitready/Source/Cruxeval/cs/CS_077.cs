using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string character) {
        int index = text.LastIndexOf(character);
        string subject = index != -1 ? text.Substring(index) : "";
        int count = text.Count(f => (f.ToString() == character));
        return string.Concat(Enumerable.Repeat(subject, count));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("h ,lpvvkohh,u"), ("i")).Equals(("")));
    }

}
