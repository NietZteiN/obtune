using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Problem {
    public static string F(string text, string value) {
        var new_text = new List<char>(text.ToCharArray());
        int length = 0;
        try
        {
            new_text.Add(Char.Parse(value));
            length = new_text.Count;
        }
        catch (IndexOutOfRangeException)
        {
            length = 0;
        }
        return "[" + length.ToString() + "]";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("abv"), ("a")).Equals(("[4]")));
    }

}
