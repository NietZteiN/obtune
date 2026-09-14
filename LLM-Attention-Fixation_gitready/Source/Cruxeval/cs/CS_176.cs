using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string to_place) {
        int index = text.IndexOf(to_place);
        string after_place = text.Substring(0, index + 1);
        string before_place = text.Substring(index + 1);
        return after_place + before_place;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("some text"), ("some")).Equals(("some text")));
    }

}
