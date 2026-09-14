using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Problem {
    public static string F(string mess, string character) {
        while (mess.IndexOf(character, mess.LastIndexOf(character) + 1) != -1)
        {
            mess = mess.Substring(0, mess.LastIndexOf(character) + 1) + mess.Substring(mess.LastIndexOf(character) + 2);
        }
        return mess;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("0aabbaa0b"), ("a")).Equals(("0aabbaa0b")));
    }

}
