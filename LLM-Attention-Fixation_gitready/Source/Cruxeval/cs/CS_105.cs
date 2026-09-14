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
        if (!CultureInfo.CurrentCulture.TextInfo.ToTitleCase(text).Equals(text))
        {
            return CultureInfo.CurrentCulture.TextInfo.ToTitleCase(text);
        }
        return text.ToLower();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("PermissioN is GRANTed")).Equals(("Permission Is Granted")));
    }

}
