using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        return text[text.Length - 1] + text.Substring(0, text.Length - 1);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("hellomyfriendear")).Equals(("rhellomyfriendea")));
    }

}
