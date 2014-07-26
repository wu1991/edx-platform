class @MarkdownEditingDescriptor extends XModule.Descriptor
  # TODO really, these templates should come from or also feed the cheatsheet
  @multipleChoiceTemplate : "( ) incorrect\n( ) incorrect\n(x) correct\n"
  @checkboxChoiceTemplate: "[x] correct\n[ ] incorrect\n[x] correct\n"
  @stringInputTemplate: "= answer\n"
  @numberInputTemplate: "= answer +- 0.001%\n"
  @selectTemplate: "[[incorrect, (correct), incorrect]]\n"
  @headerTemplate: "Header\n=====\n"
  @explanationTemplate: "[explanation]\nShort explanation\n[explanation]\n"
  @customLabel: ""

  constructor: (element) ->
    @element = element

    if $(".markdown-box", @element).length != 0
      @markdown_editor = CodeMirror.fromTextArea($(".markdown-box", element)[0], {
      lineWrapping: true
      mode: null
      })
      @setCurrentEditor(@markdown_editor)
      # Add listeners for toolbar buttons (only present for markdown editor)
      @element.on('click', '.xml-tab', @onShowXMLButton)
      @element.on('click', '.format-buttons a', @onToolbarButton)
      @element.on('click', '.cheatsheet-toggle', @toggleCheatsheet)
      # Hide the XML text area
      $(@element.find('.xml-box')).hide()
    else
      @createXMLEditor()

  ###
  Creates the XML Editor and sets it as the current editor. If text is passed in,
  it will replace the text present in the HTML template.

  text: optional argument to override the text passed in via the HTML template
  ###
  createXMLEditor: (text) ->
    @xml_editor = CodeMirror.fromTextArea($(".xml-box", @element)[0], {
    mode: "xml"
    lineNumbers: true
    lineWrapping: true
    })
    if text
      @xml_editor.setValue(text)
    @setCurrentEditor(@xml_editor)

  ###
  User has clicked to show the XML editor. Before XML editor is swapped in,
  the user will need to confirm the one-way conversion.
  ###
  onShowXMLButton: (e) =>
    e.preventDefault();
    if @cheatsheet && @cheatsheet.hasClass('shown')
      @cheatsheet.toggleClass('shown')
      @toggleCheatsheetVisibility()
    if @confirmConversionToXml()
      @createXMLEditor(MarkdownEditingDescriptor.markdownToXml(@markdown_editor.getValue()))
      # Need to refresh to get line numbers to display properly (and put cursor position to 0)
      @xml_editor.setCursor(0)
      @xml_editor.refresh()
      # Hide markdown-specific toolbar buttons
      $(@element.find('.editor-bar')).hide()

  ###
  Have the user confirm the one-way conversion to XML.
  Returns true if the user clicked OK, else false.
  ###
  confirmConversionToXml: ->
    # TODO: use something besides a JavaScript confirm dialog?
    return confirm("If you use the Advanced Editor, this problem will be converted to XML and you will not be able to return to the Simple Editor Interface.\n\nProceed to the Advanced Editor and convert this problem to XML?")

  ###
  Event listener for toolbar buttons (only possible when markdown editor is visible).
  ###
  onToolbarButton: (e) =>
    e.preventDefault();
    selection = @markdown_editor.getSelection()
    revisedSelection = null
    switch $(e.currentTarget).attr('class')
      when "multiple-choice-button" then revisedSelection = MarkdownEditingDescriptor.insertMultipleChoice(selection)
      when "string-button" then revisedSelection = MarkdownEditingDescriptor.insertStringInput(selection)
      when "number-button" then revisedSelection = MarkdownEditingDescriptor.insertNumberInput(selection)
      when "checks-button" then revisedSelection = MarkdownEditingDescriptor.insertCheckboxChoice(selection)
      when "dropdown-button" then revisedSelection = MarkdownEditingDescriptor.insertSelect(selection)
      when "header-button" then revisedSelection = MarkdownEditingDescriptor.insertHeader(selection)
      when "explanation-button" then revisedSelection = MarkdownEditingDescriptor.insertExplanation(selection)
      else # ignore click

    if revisedSelection != null
      @markdown_editor.replaceSelection(revisedSelection)
      @markdown_editor.focus()

  ###
  Event listener for toggling cheatsheet (only possible when markdown editor is visible).
  ###
  toggleCheatsheet: (e) =>
    e.preventDefault();
    if !$(@markdown_editor.getWrapperElement()).find('.simple-editor-cheatsheet')[0]
      @cheatsheet = $($('#simple-editor-cheatsheet').html())
      $(@markdown_editor.getWrapperElement()).append(@cheatsheet)

    @toggleCheatsheetVisibility()

    setTimeout (=> @cheatsheet.toggleClass('shown')), 10


  ###
  Function to toggle cheatsheet visibility.
  ###
  toggleCheatsheetVisibility: () =>
    $('.modal-content').toggleClass('cheatsheet-is-shown')

  ###
  Stores the current editor and hides the one that is not displayed.
  ###
  setCurrentEditor: (editor) ->
    if @current_editor
      $(@current_editor.getWrapperElement()).hide()
    @current_editor = editor
    $(@current_editor.getWrapperElement()).show()
    $(@current_editor).focus();

  ###
  Called when save is called. Listeners are unregistered because editing the block again will
  result in a new instance of the descriptor. Note that this is NOT the case for cancel--
  when cancel is called the instance of the descriptor is reused if edit is selected again.
  ###
  save: ->
    @element.off('click', '.xml-tab', @changeEditor)
    @element.off('click', '.format-buttons a', @onToolbarButton)
    @element.off('click', '.cheatsheet-toggle', @toggleCheatsheet)
    if @current_editor == @markdown_editor
        {
            data: MarkdownEditingDescriptor.markdownToXml(@markdown_editor.getValue())
            metadata:
            	markdown: @markdown_editor.getValue()
        }
    else
       {
          data: @xml_editor.getValue()
          nullout: ['markdown']
       }

  @insertMultipleChoice: (selectedText) ->
    return MarkdownEditingDescriptor.insertGenericChoice(selectedText, '(', ')', MarkdownEditingDescriptor.multipleChoiceTemplate)

  @insertCheckboxChoice: (selectedText) ->
    return MarkdownEditingDescriptor.insertGenericChoice(selectedText, '[', ']', MarkdownEditingDescriptor.checkboxChoiceTemplate)

  @insertGenericChoice: (selectedText, choiceStart, choiceEnd, template) ->
    if selectedText.length > 0
      # Replace adjacent newlines with a single newline, strip any trailing newline
      cleanSelectedText = selectedText.replace(/\n+/g, '\n').replace(/\n$/,'')
      lines =  cleanSelectedText.split('\n')
      revisedLines = ''
      for line in lines
        revisedLines += choiceStart
        # a stand alone x before other text implies that this option is "correct"
        if /^\s*x\s+(\S)/i.test(line)
          # Remove the x and any initial whitespace as long as there's more text on the line
          line = line.replace(/^\s*x\s+(\S)/i, '$1')
          revisedLines += 'x'
        else
          revisedLines += ' '
        revisedLines += choiceEnd + ' ' + line + '\n'
      return revisedLines
    else
      return template

  @insertStringInput: (selectedText) ->
    return MarkdownEditingDescriptor.insertGenericInput(selectedText, '= ', '', MarkdownEditingDescriptor.stringInputTemplate)

  @insertNumberInput: (selectedText) ->
    return MarkdownEditingDescriptor.insertGenericInput(selectedText, '= ', '', MarkdownEditingDescriptor.numberInputTemplate)

  @insertSelect: (selectedText) ->
    return MarkdownEditingDescriptor.insertGenericInput(selectedText, '[[', ']]', MarkdownEditingDescriptor.selectTemplate)

  @insertHeader: (selectedText) ->
    return MarkdownEditingDescriptor.insertGenericInput(selectedText, '', '\n====\n', MarkdownEditingDescriptor.headerTemplate)

  @insertExplanation: (selectedText) ->
    return MarkdownEditingDescriptor.insertGenericInput(selectedText, '[explanation]\n', '\n[explanation]', MarkdownEditingDescriptor.explanationTemplate)

  @insertGenericInput: (selectedText, lineStart, lineEnd, template) ->
    if selectedText.length > 0
      # TODO: should this insert a newline afterwards?
      return lineStart + selectedText + lineEnd
    else
      return template



  #________________________________________________________________________________
  @insertBooleanHints: (xmlStringUnderConstruction) ->
    if MarkdownEditingDescriptor.problemHintsBooleanExpressions
      index = 0
      for booleanExpression in MarkdownEditingDescriptor.problemHintsBooleanExpressions
        hintText = MarkdownEditingDescriptor.problemHintsBooleanStrings[index]
        booleanHintElement  = '        <booleanhint value="' + booleanExpression + '">' + hintText + '\n'
        booleanHintElement += '        </booleanhint>\n'
        xmlStringUnderConstruction += booleanHintElement
        index = index + 1
    return xmlStringUnderConstruction

  #________________________________________________________________________________
  @parseForCompoundConditionHints: (xmlString) ->
    for line in xmlString.split('\n')
      matches = @matchCompoundConditionPattern( line )      # string surrounded by {{...}} is a match group
      if matches
        questionHintString = matches[1]
        splitMatches = @matchBooleanConditionPattern(questionHintString)   # surrounded by ((...)) is a boolean condition
        if splitMatches
          booleanExpression = splitMatches[1]
          hintText = splitMatches[2]
          MarkdownEditingDescriptor.problemHintsBooleanStrings.push(hintText)
          MarkdownEditingDescriptor.problemHintsBooleanExpressions.push(booleanExpression)
    return xmlString

#________________________________________________________________________________
  @matchCompoundConditionPattern: (testString) ->
    return testString.match( /\{\{(.+)\}\}/ )

  #________________________________________________________________________________
  @matchBooleanConditionPattern: (testString) ->
    return testString.match( /\(\((.+)\)\)(.+)/ )

  #________________________________________________________________________________
  @matchMultipleChoicePattern: (testString) ->
    return testString.match( /\s+\(\s*x?\s*\)[^\n]+/ )

  #________________________________________________________________________________
  @matchCheckboxMarkerPattern: (testString) ->
    return testString.match( /(\s+\[\s*x?\s*\])(.+)[^\n]+/ )

  #________________________________________________________________________________
  @insertParagraphText: (xmlString, reducedXmlString) ->
      returnXmlString = ''
      for line in reducedXmlString.split('\n')
        trimmedLine = line.trim()
        if trimmedLine.length > 0
          compoundConditionMatches = @matchCompoundConditionPattern( line )      # string surrounded by {{...}} is a match group
          if compoundConditionMatches == null
            returnXmlString += '<p>\n'
            returnXmlString += trimmedLine
            returnXmlString += '</p>\n'
      return returnXmlString

  #________________________________________________________________________________
  # check a hint string for a custom label (e.g., 'NOPE::you got this answer wrong')
  # if found, remove the label and the :: delimiter and save the label in the
  # 'customLabel' variable for later handling
  #
  @extractCustomLabel: (feedbackString) ->
    returnString = feedbackString                     # assume we will find no custom label
    tokens = feedbackString.split('::')
    if tokens.length > 1                              # check for a custom label to precede the feedback string
      @customLabel = ' label="' + tokens[0] + '"'    # save the custom label for insertion into the XML
      returnString = tokens[1]
    else
      @customLabel = ' '
    return returnString                               # return the feedback string but without the custom label, if any

  #________________________________________________________________________________
  # search for any text demarcated as a 'problem hint' by the double vertical bars
  # if found, copy the text to an array for later insertion and remove that text
  # from the xmlString
  #
  @parseForProblemHints: (xmlString) ->
    MarkdownEditingDescriptor.problemHintsStrings = []    # initialize the strings array
    for line in xmlString.split('\n')
      matches = line.match( /\|\|(.+)\|\|/ )      # string surrounded by ||...|| is a match group
      if matches
        problemHint = matches[1]
        MarkdownEditingDescriptor.problemHintsStrings.push(problemHint)
        xmlString = xmlString.replace(matches[0], '')                     # strip out the matched text from the xml
    return xmlString

  #________________________________________________________________________________
  # if any 'problem hint' entries were saved in the array, insert the 'demandhint'
  # element to the xml with a 'hint' element for each item
  #
  @insertProblemHints: (xmlStringUnderConstruction) ->
    if MarkdownEditingDescriptor.problemHintsStrings
      if MarkdownEditingDescriptor.problemHintsStrings.length > 0
        ondemandElement =  '    <demandhint>\n'
        for problemHint in MarkdownEditingDescriptor.problemHintsStrings
          ondemandElement += '        <hint> ' +  problemHint + '\n'
          ondemandElement += '        </hint>\n'
        ondemandElement +=  '    </demandhint>\n'
        xmlStringUnderConstruction += ondemandElement
    return xmlStringUnderConstruction

  #________________________________________________________________________________
  @parseForDropdown: (xmlString) ->
    # try to parse the supplied string to find a drop down problem
    # return the string unmodified if this is not a drop down problem
    dropdownMatches = xmlString.match( /\[\[([^\]]+)\]\]/ )   # try to match an opening and closing double bracket

    if dropdownMatches                            # the xml has an opening and closing double bracket [[...]]
      reducedXmlString = xmlString.replace(dropdownMatches[0], '')
      returnXmlString = MarkdownEditingDescriptor.insertParagraphText(xmlString, reducedXmlString)
      returnXmlString +=  '    <optionresponse>\n'
      returnXmlString += '        <optioninput options="OPTIONS_PLACEHOLDER" correct="CORRECT_PLACEHOLDER">\n'

      optionsString = ''
      delimiter = ''
      for line in dropdownMatches[1].split( /[,\n]/)    # split the string between [[..]] brackets into single lines
        line = line.trim()
        if line.length > 0
          hintText = ''
          correctnessText = ''
          itemText = ''

          hintMatches = line.match( /{{(.+)}}/ )  # extract the {{...}} phrase, if any
          if hintMatches
            matchString = hintMatches[0]          # group 0 holds the entire matching string (includes delimiters)
            hintText = hintMatches[1].trim()      # group 1 holds the matching characters (our string)
            hintText = @extractCustomLabel( hintText )
            line = line.replace(matchString, '')  # remove the {{...}} phrase, else it will be displayed to student

          correctChoiceMatch = line.match( /^\s*\(([^)]+)\)/ )  # try to match a parenthetical string: '(...)'
          if correctChoiceMatch                          # matched so this must be the correct answer
            correctnessText = 'True'
            itemText = correctChoiceMatch[1]
            returnXmlString = returnXmlString.replace('CORRECT_PLACEHOLDER', itemText)  # poke the correct value in
            optionsString += delimiter + '(' + itemText + ')'
          else
            correctnessText = 'False'
            itemText = line
            optionsString += delimiter + itemText.trim()

          if itemText[itemText.length-1] == ','     # check for an end-of-line comma
            itemText = itemText.slice(0, itemText.length-1) # suppress it
          itemText = itemText.trim()

          returnXmlString += '              <option  correct="' + correctnessText + '">'
          returnXmlString += '                  ' + itemText + '\n'
          if hintText
            returnXmlString += '                   <optionhint ' + @customLabel + '>' + hintText + '\n'
            returnXmlString += '                   </optionhint>\n'
          returnXmlString += '              </option>\n'

          delimiter = ', '

      returnXmlString += '        </optioninput>\n'
      returnXmlString = returnXmlString.replace('OPTIONS_PLACEHOLDER', optionsString)  # poke the options in
      MarkdownEditingDescriptor.parseForCompoundConditionHints(xmlString)  # pull out any compound condition hints
      returnXmlString = MarkdownEditingDescriptor.insertBooleanHints(returnXmlString)
      returnXmlString += '    </optionresponse>\n'
    else
      returnXmlString = xmlString

    return returnXmlString

















# We may wish to add insertHeader. Here is Tom's code.
# function makeHeader() {
#  var selection = simpleEditor.getSelection();
#  var revisedSelection = selection + '\n';
#  for(var i = 0; i < selection.length; i++) {
#revisedSelection += '=';
#  }
#  simpleEditor.replaceSelection(revisedSelection);
#}
#
  @markdownToXml: (markdown)->
    toXml = `function (markdown) {
      var xml = markdown,
          i, splits, scriptFlag;

      // replace headers
      xml = xml.replace(/(^.*?$)(?=\n\=\=+$)/gm, '<h1>$1</h1>');
      xml = xml.replace(/\n^\=\=+$/gm, '');

      xml = MarkdownEditingDescriptor.parseForProblemHints(xml);    // pull out any problem hints






      //---------------------------------------------------------------------------
      // multiple choice questions
      //
      xml = xml.replace(/(^\s*\(.{0,3}\).*?$\n*)+/gm, function(match, p) {
        var choices = '';
        var shuffle = false;
        var options = match.split('\n');

        for(var i = 0; i < options.length; i++) {
          line = options[i].trim();               // trim off leading/trailing whitespace
          if(line.length > 0) {
            hintText = '';
            hintMatches = line.match( /{{(.+)}}/ );  // extract the {{...}} phrase, if any
            if(hintMatches) {
              matchString = hintMatches[0];          // group 0 holds the entire matching string (includes delimiters)
              hintText = hintMatches[1].trim();      // group 1 holds the matching characters (our hint string)
              hintText = MarkdownEditingDescriptor.extractCustomLabel( hintText );
              line = line.replace(matchString, '');  // remove the {{...}} phrase, else it will be displayed
            }

            var value = line.split(/^\s*\(.{0,3}\)\s*/)[1];
            var inparens = /^\s*\((.{0,3})\)\s*/.exec(line)[1];
            var correct = /x/i.test(inparens);
            var fixed = '';
            if(/@/.test(inparens)) {
              fixed = ' fixed="true"';
            }
            if(/!/.test(inparens)) {
              shuffle = true;
            }
            choices += '    <choice correct="' + correct + '"' + fixed + '>' + value + '\n';
            if(hintText) {
              choices += '        <choicehint ' + MarkdownEditingDescriptor.customLabel + '>' + hintText + '\n'
              choices += '        </choicehint>\n'
            }
            choices += '    </choice>\n';
          }
        }
        var result = '<multiplechoiceresponse>\n';
        if(shuffle) {
          result += '  <choicegroup type="MultipleChoice" shuffle="true">\n';
        }
        else {
          result += '  <choicegroup type="MultipleChoice">\n';
        }
        result += choices;
        result += '  </choicegroup>\n';
        result += '</multiplechoiceresponse>\n\n';
        return result;
      });








      //---------------------------------------------------------------------------
      // checkbox questions
      xml = xml.replace(/(^\s*\[.?\].*?$\n*)+/gm, function(match) {
          var groupString = '<choiceresponse>\n',
              options, value, correct;

          groupString += '  <checkboxgroup direction="vertical">\n';
          options = match.split('\n');

          for (i = 0; i < options.length; i += 1) {
              if(line.length > 0) {
                  value = line.split(/^\s*\[.?\]\s*/)[1];
                  correct = /^\s*\[x\]/i.test(line);
                  groupString += '    <choice correct="' + correct + '">' + value + '</choice>\n';
              }
          }

          groupString += '  </checkboxgroup>\n';
          groupString += '</choiceresponse>\n\n';

          return groupString;
      });

      //---------------------------------------------------------------------------
      // text input and numeric input questions
      xml = xml.replace(/(^\=\s*(.*?$)(\n*or\=\s*(.*?$))*)+/gm, function(match, p) {
          // Split answers
          var answersList = p.replace(/^(or)?=\s*/gm, '').split('\n'),

              processNumericalResponse = function (value) {
                  var params, answer, string;

                  if (_.contains([ '[', '(' ], value[0]) && _.contains([ ']', ')' ], value[value.length-1]) ) {
                    // [5, 7) or (5, 7), or (1.2345 * (2+3), 7*4 ]  - range tolerance case
                    // = (5*2)*3 should not be used as range tolerance
                    string = '<numericalresponse answer="' + value +  '">\n';
                    string += '  <formulaequationinput />\n';
                    string += '</numericalresponse>\n\n';
                    return string;
                  }

                  if (isNaN(parseFloat(value))) {
                      return false;
                  }

                  // Tries to extract parameters from string like 'expr +- tolerance'
                  params = /(.*?)\+\-\s*(.*?$)/.exec(value);

                  if(params) {
                      answer = params[1].replace(/\s+/g, ''); // support inputs like 5*2 +- 10
                      string = '<numericalresponse answer="' + answer + '">\n';
                      string += '  <responseparam type="tolerance" default="' + params[2] + '" />\n';
                  } else {
                      answer = value.replace(/\s+/g, ''); // support inputs like 5*2
                      string = '<numericalresponse answer="' + answer + '">\n';
                  }

                  string += '  <formulaequationinput />\n';
                  string += '</numericalresponse>\n\n';

                  return string;
              },

              processStringResponse = function (values) {
                  var firstAnswer = values.shift(), string;

                  if (firstAnswer[0] === '|') { // this is regexp case
                      string = '<stringresponse answer="' + firstAnswer.slice(1).trim() +  '" type="ci regexp" >\n';
                  } else {
                      string = '<stringresponse answer="' + firstAnswer +  '" type="ci" >\n';
                  }

                  for (i = 0; i < values.length; i += 1) {
                      string += '  <additional_answer>' + values[i] + '</additional_answer>\n';
                  }

                  string +=  '  <textline size="20"/>\n</stringresponse>\n\n';

                  return string;
              };

          return processNumericalResponse(answersList[0]) || processStringResponse(answersList);
      });





      //---------------------------------------------------------------------------
      // dropdown questions
      //
      xml = xml.replace(/\[\[([^\]]+)\]\]/gm, function(match, p) {
        return MarkdownEditingDescriptor.parseForDropdown(match);
      });














      // replace explanations
      xml = xml.replace(/\[explanation\]\n?([^\]]*)\[\/?explanation\]/gmi, function(match, p1) {
          var selectString = '<solution>\n<div class="detailed-solution">\nExplanation\n\n' + p1 + '\n</div>\n</solution>';

          return selectString;
      });
      
      // replace labels
      // looks for >>arbitrary text<< and inserts it into the label attribute of the input type directly below the text. 
      var split = xml.split('\n');
      var new_xml = [];
      var line, i, curlabel, prevlabel = '';
      var didinput = false;
      for (i = 0; i < split.length; i++) {
        line = split[i];
        if (match = line.match(/>>(.*)<</)) {
          curlabel = match[1].replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&apos;');
          line = line.replace(/>>|<</g, '');
        } else if (line.match(/<\w+response/) && didinput && curlabel == prevlabel) {
          // reset label to prevent gobbling up previous one (if multiple questions)
          curlabel = '';
          didinput = false;
        } else if (line.match(/<(textline|optioninput|formulaequationinput|choicegroup|checkboxgroup)/) && curlabel != '' && curlabel != undefined) {
          line = line.replace(/<(textline|optioninput|formulaequationinput|choicegroup|checkboxgroup)/, '<$1 label="' + curlabel + '"');
          didinput = true;
          prevlabel = curlabel;
        }
        new_xml.push(line);
      }
      xml = new_xml.join('\n');

      // replace code blocks
      xml = xml.replace(/\[code\]\n?([^\]]*)\[\/?code\]/gmi, function(match, p1) {
          var selectString = '<pre><code>\n' + p1 + '</code></pre>';

          return selectString;
      });

      // split scripts and preformatted sections, and wrap paragraphs
      splits = xml.split(/(\<\/?(?:script|pre).*?\>)/g);
      scriptFlag = false;

      for (i = 0; i < splits.length; i += 1) {
          if(/\<(script|pre)/.test(splits[i])) {
              scriptFlag = true;
          }

          if(!scriptFlag) {
              splits[i] = splits[i].replace(/(^(?!\s*\<|$).*$)/gm, '<p>$1</p>');
          }

          if(/\<\/(script|pre)/.test(splits[i])) {
              scriptFlag = false;
          }
      }

      xml = splits.join('');

      // rid white space
      xml = xml.replace(/\n\n\n/g, '\n');

      xml = MarkdownEditingDescriptor.insertProblemHints(xml);      // insert any extracted problem hints

      // make all elements descendants of a single problem element
      xml = '<problem schema="edXML/1.0">\n' + xml + '\n</problem>';

      return xml;
    }`
    return toXml markdown

