using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string to_remove) {
        var new_text = text.ToCharArray().ToList();
        if(new_text.Contains(to_remove[0]))
        {
            int index = new_text.IndexOf(to_remove[0]);
            new_text.Remove(to_remove[0]);
            new_text.Insert(index, '?');
            new_text.Remove('?');
        }
        return string.Join("", new_text);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("sjbrlfqmw"), ("l")).Equals(("sjbrfqmw")));
    }

}
