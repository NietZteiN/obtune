using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string[] items = text.Split();
        foreach (var item in items)
        {
            text = text.Replace($"-{item}", " ").Replace($"{item}-", " ");
        }
        return text.Trim('-');
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("-stew---corn-and-beans-in soup-.-")).Equals(("stew---corn-and-beans-in soup-.")));
    }

}
